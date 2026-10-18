/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 University of Washington
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as 
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef TWO_STATE_PROPAGATION_LOSS_MODEL_H
#define TWO_STATE_PROPAGATION_LOSS_MODEL_H

#include "ns3/object.h"
#include "ns3/nstime.h"
#include "ns3/random-variable-stream.h"
#include "ns3/propagation-loss-model.h"

namespace ns3 {

class MobilityModel;

/**
 * \ingroup propagation
 *
 * \brief The propagation loss varies based on a two-state Markov model,
 *        independent of the frequency, distance, or other factors.
 *
 * The channel is in a good or bad state for exponentially distributed
 * amounts of time.  In a good state, the channel loss rate is PER_g.
 * In a bad state, the channel loss rate is PER_b.  The channel starts
 * in a good state.
 *
 * When a packet is errored, its power is set to an extremely low value
 * (-1000 dBm, effectively zero).  When a packet is not errored, its power
 * is unchanged.
*/
class TwoStatePropagationLossModel : public PropagationLossModel
{
public:
  /**
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);
  TwoStatePropagationLossModel ();

  // These setters and getters facilitate the configuration of random variables
  void SetPerG (double per);
  double GetPerG (void) const;

  void SetPerB (double per);
  double GetPerB (void) const;

  void SetGammaG (Time t);
  Time GetGammaG (void) const;

  void SetGammaB (Time t);
  Time GetGammaB (void) const;

private:
  /**
   * \brief Copy constructor
   *
   * Defined and unimplemented to avoid misuse
   */
  TwoStatePropagationLossModel (const TwoStatePropagationLossModel&);
  /**
   * \brief Copy constructor
   *
   * Defined and unimplemented to avoid misuse
   */
  TwoStatePropagationLossModel& operator= (const TwoStatePropagationLossModel&);

  virtual double DoCalcRxPower (double txPowerDbm,
                                Ptr<MobilityModel> a,
                                Ptr<MobilityModel> b) const;

  void SwitchState (void);

  virtual void Start (void);

  virtual int64_t DoAssignStreams (int64_t stream);

private:
  Ptr<ExponentialRandomVariable> m_ranVarGoodDuration;
  Ptr<ExponentialRandomVariable> m_ranVarBadDuration;
  Ptr<UniformRandomVariable> m_ranVarPerGood;
  Ptr<UniformRandomVariable> m_ranVarPerBad;

  double m_perGood {0};
  double m_perBad {0};
  bool m_goodState {true};
};

} // namespace ns3

#endif /* TWO_STATE_PROPAGATION_LOSS_MODEL_H */
